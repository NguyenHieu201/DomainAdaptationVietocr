from vietocr.model.backbone.cnn import CNN
from vietocr.model.seqmodel.transformer import LanguageTransformer
from vietocr.model.seqmodel.seq2seq import Seq2Seq
from vietocr.model.seqmodel.convseq2seq import ConvSeq2Seq
from torch import nn
import torch


class VietOCR(nn.Module):
    def __init__(self, vocab_size,
                 backbone,
                 cnn_args,
                 transformer_args, seq_modeling='transformer'):

        super(VietOCR, self).__init__()

        self.cnn = CNN(backbone, **cnn_args)
        self.discriminator = nn.Linear(cnn_args['hidden'], 1)
        self.seq_modeling = seq_modeling

        if seq_modeling == 'transformer':
            self.transformer = LanguageTransformer(
                vocab_size, **transformer_args)
        elif seq_modeling == 'seq2seq':
            self.transformer = Seq2Seq(vocab_size, **transformer_args)
        elif seq_modeling == 'convseq2seq':
            self.transformer = ConvSeq2Seq(vocab_size, **transformer_args)
        else:
            raise ('Not Support Seq Model')

    def forward(self, img, tgt_input, tgt_key_padding_mask,
                discriminator=False):
        """
        Shape:
            - img: (N, C, H, W)
            - tgt_input: (T, N)
            - tgt_key_padding_mask: (N, T)
            - output: b t v
        """
        src = self.cnn(img)
        if discriminator:
            # print(f"Img shape: {img.shape} Ouput shape: {src.shape}")
            temp_src = torch.sum(src, dim=0)
            # print(f"Temp src shape: {temp_src.shape}")
            discriminator_output = self.discriminator(temp_src)
            # softmax = torch.nn.Softmax(dim=0)
            # discriminator_output = softmax(discriminator_output)
            # print(discriminator_output.shape)
            # BCE_loss = nn.CrossEntropyLoss()
            # target = torch.zeros(discriminator_output.shape)
            # loss = BCE_loss(discriminator_output, target)
            return discriminator_output
        else:

            if self.seq_modeling == 'transformer':
                outputs = self.transformer(
                    src, tgt_input, tgt_key_padding_mask=tgt_key_padding_mask)
            elif self.seq_modeling == 'seq2seq':
                outputs = self.transformer(src, tgt_input)
            elif self.seq_modeling == 'convseq2seq':
                outputs = self.transformer(src, tgt_input)
            return outputs
